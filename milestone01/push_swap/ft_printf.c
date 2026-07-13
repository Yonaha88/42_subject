/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_printf.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/05/17 11:19:16 by hkanamit          #+#    #+#             */
/*   Updated: 2026/05/18 13:33:28 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "push_swap.h"

void	put_unsigned_nbr_base(unsigned int nbr, char *base, int *ret)
{
	unsigned int	letter;

	letter = 0;
	while (base[letter])
		letter++;
	if (nbr >= letter)
		put_unsigned_nbr_base(nbr / letter, base, ret);
	if (*ret == -1)
		return ;
	put_char(base[nbr % letter], ret);
	if (*ret == -1)
		return ;
}

void	put_address_2(int *ret)
{
	if (write(2, "0x", 2) == 2)
		*ret += 2;
	else
	{
		*ret = -1;
		return ;
	}
}

void	put_address(unsigned long long nbr, char *base, int *ret, int flag)
{
	size_t	letter;

	letter = 0;
	while (base[letter])
		letter++;
	if (nbr == 0)
	{
		putstr("(nil)", ret);
		return ;
	}
	if (flag == 1)
	{
		put_address_2(ret);
		if (*ret == -1)
			return ;
		flag = 0;
	}
	if (nbr >= letter)
		put_address(nbr / letter, base, ret, flag);
	if (*ret == -1)
		return ;
	put_char(base[nbr % letter], ret);
	if (*ret == -1)
		return ;
}

void	output_count(const char format, va_list args, int *ret)
{
	if (format == 'c')
		put_char((char)va_arg(args, int), ret);
	else if (format == 's')
		putstr(va_arg(args, char *), ret);
	else if (format == 'd' || format == 'i')
		put_nbr(va_arg(args, int), ret);
	else if (format == 'u')
		put_unsigned_nbr_base(va_arg(args, unsigned int), "0123456789", ret);
	else if (format == 'x')
		put_unsigned_nbr_base(va_arg(args, unsigned int), "0123456789abcdef",
			ret);
	else if (format == 'X')
		put_unsigned_nbr_base(va_arg(args, unsigned int), "0123456789ABCDEF",
			ret);
	else if (format == 'p')
		put_address((unsigned long long)va_arg(args, void *),
			"0123456789abcdef", ret, 1);
	else if (format == '%')
		put_char('%', ret);
	else
		put_per_something(format, ret);
}

int	ft_printf(const char *format, ...)
{
	va_list	args;
	int		ret;
	int		i;

	i = 0;
	va_start(args, format);
	ret = 0;
	while (format[i])
	{
		if (format[i] == '%' && format[i + 1])
			output_count(format[++i], args, &ret);
		else
			put_char(format[i], &ret);
		if (ret < 0)
			break ;
		i++;
	}
	va_end(args);
	return (ret);
}
