/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_striteri.c                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/29 14:25:13 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/03 10:56:10 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	ft_striteri(char *s, void (*f)(unsigned int, char*))
{
	unsigned int	idx;
	unsigned int	s_len;

	idx = 0;
	s_len = (unsigned int)ft_strlen(s);
	while (idx < s_len)
	{
		f(idx, s + idx);
		idx++;
	}
}
