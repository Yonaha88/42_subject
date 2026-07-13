/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_itoa.c                                          :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/28 15:50:23 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:18:16 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

static int	count_digits(long nbr)
{
	int	digit;

	digit = 0;
	if (nbr < 0)
		digit++;
	if (nbr == 0)
		digit++;
	while (nbr)
	{
		nbr /= 10;
		digit++;
	}
	return (digit);
}

static void	fill_numptr(char *numptr, long nbr, int digit)
{
	int	idx;

	idx = digit;
	numptr[idx] = '\0';
	idx--;
	if (nbr < 0)
	{
		numptr[0] = '-';
		nbr = -nbr;
	}
	if (nbr == 0)
		numptr[idx] = '0';
	while (nbr > 0)
	{
		numptr[idx] = '0' + (nbr % 10);
		nbr /= 10;
		idx--;
	}
}

char	*ft_itoa(int n)
{
	char	*numptr;
	long	nbr;
	int		digit;

	nbr = n;
	digit = count_digits(nbr);
	numptr = (char *)malloc((digit + 1) * sizeof(char));
	if (numptr == NULL)
		return (NULL);
	fill_numptr(numptr, nbr, digit);
	return (numptr);
}
